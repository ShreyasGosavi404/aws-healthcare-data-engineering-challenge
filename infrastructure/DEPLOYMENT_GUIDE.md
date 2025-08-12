# CloudFormation Deployment Guide

## Issue Diagnosis

Your CloudFormation stack `healthcare-analytics-challenge` failed with **ROLLBACK_COMPLETE** status. This typically indicates one of these issues:

### Common Causes:
1. **IAM Role Name Conflicts** - Explicit role names already exist
2. **Missing Required Parameters** - NotificationEmail parameter not provided
3. **Resource Naming Conflicts** - Resources with same names already exist
4. **Permission Issues** - Insufficient permissions to create resources

## 🔧 Fixed Issues

### 1. Removed Explicit Role Names
**Problem**: `RoleName` properties cause conflicts on redeployment
```yaml
# ❌ Before (causes conflicts)
RoleName: !Sub '${ProjectName}-lambda-execution-role-${Environment}'

# ✅ After (auto-generated names)
# (removed RoleName property entirely)
```

### 2. Added Missing EventBridge Role
**Problem**: EventBridge rule had insufficient permissions
```yaml
# ✅ Added new role for EventBridge
EventBridgeRole:
  Type: 'AWS::IAM::Role'
  Properties:
    AssumeRolePolicyDocument:
      # ... EventBridge service principal
```

### 3. Made NotificationEmail Optional
**Problem**: Required parameter without default value
```yaml
# ✅ Added default value
NotificationEmail:
  Type: String
  Default: 'admin@example.com'  # Added this line
```

## 🚀 Deployment Options

### Option 1: Use Fixed Template (Recommended)
Deploy the corrected `healthcare-infrastructure.yaml`:

```bash
aws cloudformation create-stack \
  --stack-name healthcare-analytics-fixed \
  --template-body file://infrastructure/healthcare-infrastructure.yaml \
  --parameters ParameterKey=NotificationEmail,ParameterValue=your.email@example.com \
  --capabilities CAPABILITY_IAM
```

### Option 2: Use Simplified Template (Safer)
Deploy the minimal `healthcare-infrastructure-simple.yaml`:

```bash
aws cloudformation create-stack \
  --stack-name healthcare-analytics-simple \
  --template-body file://infrastructure/healthcare-infrastructure-simple.yaml \
  --capabilities CAPABILITY_IAM
```

### Option 3: Manual Cleanup + Redeploy
1. **Delete the failed stack first**:
   ```bash
   aws cloudformation delete-stack --stack-name healthcare-analytics-challenge
   ```

2. **Wait for deletion to complete** (check in console)

3. **Deploy with new name**:
   ```bash
   aws cloudformation create-stack \
     --stack-name healthcare-analytics-v2 \
     --template-body file://infrastructure/healthcare-infrastructure.yaml \
     --parameters ParameterKey=NotificationEmail,ParameterValue=your.email@example.com \
     --capabilities CAPABILITY_IAM
   ```

## 📋 Pre-Deployment Checklist

### ✅ Before Deployment:
- [ ] Verify AWS CLI is configured with sufficient permissions
- [ ] Ensure the failed stack is deleted (if reusing name)
- [ ] Update NotificationEmail parameter with valid email
- [ ] Choose unique stack name
- [ ] Verify region is us-east-1 (or update template accordingly)

### 🔒 Required IAM Permissions:
Your AWS user/role needs these permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:*",
        "iam:*",
        "s3:*",
        "lambda:*",
        "states:*",
        "athena:*",
        "glue:*",
        "sns:*",
        "events:*",
        "cloudwatch:*"
      ],
      "Resource": "*"
    }
  ]
}
```

## 🎯 Recommended Approach

**For Challenge Submission**: Use the **simplified template** as it's less likely to fail:

1. Deploy the core infrastructure:
   ```bash
   aws cloudformation create-stack \
     --stack-name healthcare-challenge-core \
     --template-body file://infrastructure/healthcare-infrastructure-simple.yaml \
     --capabilities CAPABILITY_IAM
   ```

2. **Manually create additional resources** if needed:
   - Lambda functions
   - Step Functions state machines
   - EventBridge rules

3. **Document the manual steps** in your submission

## 🔍 Troubleshooting Commands

### Check Stack Status:
```bash
aws cloudformation describe-stacks --stack-name healthcare-analytics-challenge
```

### View Stack Events (Find Root Cause):
```bash
aws cloudformation describe-stack-events --stack-name healthcare-analytics-challenge
```

### List All Stacks:
```bash
aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE ROLLBACK_COMPLETE
```

### Delete Failed Stack:
```bash
aws cloudformation delete-stack --stack-name healthcare-analytics-challenge
```

## 💡 Success Indicators

### ✅ Successful Deployment Shows:
- **Status**: `CREATE_COMPLETE`
- **All Resources Created**: No failed resources in Events tab
- **Outputs Available**: All exported values populated
- **No Rollback**: No rollback events in timeline

### 📊 Expected Resources Created:
- 2-3 S3 Buckets
- 2-3 IAM Roles  
- 1 SNS Topic
- 1 Glue Database
- 1 Athena WorkGroup
- (Optional) Lambda Functions
- (Optional) Step Functions State Machine

---

## 🎯 Next Steps After Successful Deployment

1. **Note the Output Values** - You'll need these for manual resource creation
2. **Upload Test Data** to the data bucket
3. **Create Athena Table** using the provided SQL scripts
4. **Deploy Lambda Function** manually if not included
5. **Test the Pipeline** end-to-end

The core infrastructure will support your AWS Challenge implementation regardless of whether you use CloudFormation or manual deployment!
