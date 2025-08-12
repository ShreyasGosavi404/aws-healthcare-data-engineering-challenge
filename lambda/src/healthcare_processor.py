"""
Healthcare Facility Data Processor Lambda Function

This Lambda function processes healthcare facility data from S3 and identifies
facilities with expiring accreditations.
"""

import json
import boto3
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
athena_client = boto3.client('athena')
sns_client = boto3.client('sns')

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler function
    
    Args:
        event: Lambda event data
        context: Lambda context object
        
    Returns:
        Dict containing processing results
    """
    try:
        logger.info(f"Processing event: {json.dumps(event)}")
        
        # Extract S3 bucket and key from event
        bucket_name = event.get('bucket_name', 'healthcare-data-bucket')
        object_key = event.get('object_key', 'facilities/')
        
        # Process the healthcare data
        results = process_healthcare_data(bucket_name, object_key)
        
        # Check for expiring accreditations
        expiring_facilities = check_expiring_accreditations(results)
        
        # Send notifications if needed
        if expiring_facilities:
            send_notifications(expiring_facilities)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Healthcare data processed successfully',
                'facilities_processed': len(results),
                'expiring_accreditations_found': len(expiring_facilities),
                'results': results[:10]  # Return first 10 for preview
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing healthcare data: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error processing healthcare data',
                'error': str(e)
            })
        }

def process_healthcare_data(bucket_name: str, object_key: str) -> List[Dict[str, Any]]:
    """
    Process healthcare facility data from S3
    
    Args:
        bucket_name: S3 bucket name
        object_key: S3 object key/prefix
        
    Returns:
        List of processed facility records
    """
    processed_facilities = []
    
    try:
        # List objects in the S3 bucket
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=object_key
        )
        
        if 'Contents' not in response:
            logger.warning(f"No objects found in {bucket_name}/{object_key}")
            return processed_facilities
        
        # Process each JSON file
        for obj in response['Contents']:
            if obj['Key'].endswith('.json'):
                facility_data = load_facility_data(bucket_name, obj['Key'])
                if facility_data:
                    processed_data = enrich_facility_data(facility_data)
                    processed_facilities.append(processed_data)
        
        logger.info(f"Processed {len(processed_facilities)} facilities")
        return processed_facilities
        
    except Exception as e:
        logger.error(f"Error processing healthcare data: {str(e)}")
        raise

def load_facility_data(bucket_name: str, object_key: str) -> Dict[str, Any]:
    """
    Load facility data from S3 JSON file
    
    Args:
        bucket_name: S3 bucket name
        object_key: S3 object key
        
    Returns:
        Parsed facility data or empty dict if error
    """
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        content = response['Body'].read().decode('utf-8')
        return json.loads(content)
        
    except Exception as e:
        logger.error(f"Error loading facility data from {object_key}: {str(e)}")
        return {}

def enrich_facility_data(facility_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich facility data with calculated fields
    
    Args:
        facility_data: Raw facility data
        
    Returns:
        Enriched facility data
    """
    try:
        # Calculate additional metrics
        facility_data['total_services'] = len(facility_data.get('services', []))
        facility_data['total_accreditations'] = len(facility_data.get('accreditations', []))
        facility_data['total_labs'] = len(facility_data.get('labs', []))
        
        # All accreditations are considered active since no status field exists
        facility_data['active_accreditations'] = facility_data['total_accreditations']
        
        # Calculate staffing density (employees per service)
        employee_count = facility_data.get('employee_count', 0)
        service_count = facility_data['total_services']
        facility_data['employees_per_service'] = employee_count / service_count if service_count > 0 else 0
        
        # Add processing timestamp
        facility_data['processed_at'] = datetime.utcnow().isoformat()
        
        return facility_data
        
    except Exception as e:
        logger.error(f"Error enriching facility data: {str(e)}")
        return facility_data

def check_expiring_accreditations(facilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Check for facilities with expiring accreditations
    
    Args:
        facilities: List of facility records
        
    Returns:
        List of facilities with expiring accreditations
    """
    expiring_facilities = []
    current_date = datetime.now()
    warning_threshold = current_date + timedelta(days=90)
    
    try:
        for facility in facilities:
            facility_expiring = []
            
            for accreditation in facility.get('accreditations', []):
                # All accreditations are considered active since no status field
                valid_until_str = accreditation.get('valid_until')
                if valid_until_str:
                    valid_until_date = datetime.strptime(valid_until_str, '%Y-%m-%d')
                    
                    if valid_until_date <= warning_threshold:
                        days_to_expiry = (valid_until_date - current_date).days
                        
                        # Determine priority level
                        if days_to_expiry <= 30:
                            priority = 'Critical'
                        elif days_to_expiry <= 60:
                            priority = 'High'
                        else:
                            priority = 'Medium'
                        
                        facility_expiring.append({
                            'accreditation_body': accreditation.get('accreditation_body'),
                            'accreditation_id': accreditation.get('accreditation_id'),
                            'valid_until': valid_until_str,
                            'days_to_expiry': days_to_expiry,
                            'priority': priority
                        })
            
            if facility_expiring:
                expiring_facilities.append({
                    'facility_id': facility.get('facility_id'),
                    'facility_name': facility.get('facility_name'),
                    'location': facility.get('location', {}),
                    'expiring_accreditations': facility_expiring
                })
        
        logger.info(f"Found {len(expiring_facilities)} facilities with expiring accreditations")
        return expiring_facilities
        
    except Exception as e:
        logger.error(f"Error checking expiring accreditations: {str(e)}")
        return []

def send_notifications(expiring_facilities: List[Dict[str, Any]]) -> None:
    """
    Send notifications for facilities with expiring accreditations
    
    Args:
        expiring_facilities: List of facilities with expiring accreditations
    """
    try:
        # Group by priority
        critical_facilities = []
        high_priority_facilities = []
        medium_priority_facilities = []
        
        for facility in expiring_facilities:
            for accred in facility['expiring_accreditations']:
                if accred['priority'] == 'Critical':
                    critical_facilities.append(facility)
                elif accred['priority'] == 'High':
                    high_priority_facilities.append(facility)
                else:
                    medium_priority_facilities.append(facility)
        
        # Send notifications based on priority
        if critical_facilities:
            send_sns_notification(
                'Critical: Healthcare Accreditations Expiring Soon',
                format_notification_message(critical_facilities, 'Critical'),
                'critical'
            )
        
        if high_priority_facilities:
            send_sns_notification(
                'High Priority: Healthcare Accreditations Expiring',
                format_notification_message(high_priority_facilities, 'High'),
                'high'
            )
        
        if medium_priority_facilities:
            send_sns_notification(
                'Medium Priority: Healthcare Accreditations Expiring',
                format_notification_message(medium_priority_facilities, 'Medium'),
                'medium'
            )
            
    except Exception as e:
        logger.error(f"Error sending notifications: {str(e)}")

def send_sns_notification(subject: str, message: str, priority: str) -> None:
    """
    Send SNS notification
    
    Args:
        subject: Email subject
        message: Email message
        priority: Priority level
    """
    try:
        topic_arn = f"arn:aws:sns:us-east-1:123456789012:healthcare-accreditation-{priority}"
        
        sns_client.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject=subject
        )
        
        logger.info(f"Sent {priority} priority notification")
        
    except Exception as e:
        logger.error(f"Error sending SNS notification: {str(e)}")

def format_notification_message(facilities: List[Dict[str, Any]], priority: str) -> str:
    """
    Format notification message
    
    Args:
        facilities: List of facilities
        priority: Priority level
        
    Returns:
        Formatted message string
    """
    message_lines = [
        f"Healthcare Accreditation Alert - {priority} Priority",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"The following healthcare facilities have {priority.lower()} priority accreditations expiring:",
        ""
    ]
    
    for facility in facilities:
        message_lines.append(f"Facility: {facility['facility_name']}")
        message_lines.append(f"Location: {facility['location'].get('city', 'N/A')}, {facility['location'].get('state', 'N/A')}")
        
        for accred in facility['expiring_accreditations']:
            if accred['priority'] == priority:
                message_lines.append(f"  - {accred['accreditation_type']} (expires in {accred['days_to_expiry']} days)")
        
        message_lines.append("")
    
    message_lines.append("Please take immediate action to renew these accreditations.")
    
    return "\n".join(message_lines)
