aws s3 --region us-east-1 sync --cache-control no-cache --exclude "*" --include "*.html" site s3://b3denv.com
aws s3 --region us-east-1 sync --exclude "*.html" site s3://b3denv.com