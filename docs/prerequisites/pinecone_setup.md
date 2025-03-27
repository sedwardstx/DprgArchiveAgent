# Setting Up Pinecone

DprgArchiveAgent uses Pinecone for vector database storage. This guide walks you through setting up a Pinecone account and obtaining the necessary API keys.

## What is Pinecone?

[Pinecone](https://www.pinecone.io/) is a managed vector database service that makes it easy to build high-performance vector search applications. DprgArchiveAgent uses Pinecone to store and query vector embeddings for the DPRG archive.

## Creating a Pinecone Account

1. **Visit the Pinecone website**:
   - Go to [https://www.pinecone.io/](https://www.pinecone.io/)
   - Click on "Get Started" or "Sign Up" button

2. **Sign up for an account**:
   - You can sign up using:
     - Email and password
     - Google account
     - GitHub account
   - Follow the on-screen instructions to complete the signup process

3. **Verify your email** (if required):
   - Check your inbox for a verification email from Pinecone
   - Click the verification link to confirm your account

## Choosing a Plan

Pinecone offers different plans with varying features and pricing:

1. **Free Tier**:
   - Suitable for development and small-scale projects
   - Limited index size and operations
   - No credit card required

2. **Paid Plans**:
   - Standard: For production applications
   - Enterprise: For large-scale deployments with additional features

For DprgArchiveAgent, the free tier is sufficient for testing and small-scale usage.

## Getting Your API Key

1. **Log in to your Pinecone Console**:
   - Go to [https://app.pinecone.io/](https://app.pinecone.io/)
   - Sign in with your credentials

2. **Navigate to API Keys**:
   - From the dashboard, look for "API Keys" in the left sidebar or under your account settings
   - Click on it to view your API keys

3. **Copy your API Key**:
   - You should see your default API key listed
   - Click the "Copy" button next to the API key
   - Keep this key secure, as it provides access to your Pinecone resources

## Finding Your Environment

In addition to the API key, you'll need your Pinecone environment:

1. **From the Pinecone Console**:
   - Look for "Environment" or "Region" information
   - This might be shown on the dashboard or in the API key section
   - Note down this value (e.g., `us-west1-gcp`, `eu-west1-aws`, etc.)

## Setting Up for DprgArchiveAgent

For DprgArchiveAgent, you'll need:
- Your Pinecone API Key
- Your Pinecone Environment

These values will be added to your `.env` file when configuring the application.

### Example Configuration

In your `.env` file, you'll add:

```
PINECONE_API_KEY=your_api_key_here
PINECONE_ENVIRONMENT=your_environment_here
```

## Pre-configured Indexes

DprgArchiveAgent is designed to work with specific pre-configured Pinecone indexes for the DPRG archive:

```
DENSE_INDEX_URL=https://dprg-list-archive-dense-4p4f7lg.svc.aped-4627-b74a.pinecone.io
SPARSE_INDEX_URL=https://dprg-list-archive-sparse-4p4f7lg.svc.aped-4627-b74a.pinecone.io
PINECONE_NAMESPACE=dprg-archive
```

These indexes have already been created and populated with the DPRG archive data, so you just need to provide your API key and environment to access them.

## Creating Your Own Indexes (Optional)

If you want to create your own Pinecone indexes for a different dataset:

1. **From the Pinecone Console**:
   - Click on "Indexes" in the navigation menu
   - Click "Create Index"

2. **Configure your index**:
   - Name: Give your index a unique name
   - Dimension: Set to the dimension of your vectors (depends on your embedding model)
   - Metric: Choose a similarity metric (e.g., cosine, dotproduct, euclidean)
   - Select your cloud provider and region

3. **Create the index**:
   - Click "Create Index" to finalize

4. **View index details**:
   - Once created, click on your index to view details
   - Note the "Host" or "URL" for the index
   - You'll need this URL to connect to your index

## Troubleshooting

### Common Issues

1. **API Key Not Working**:
   - Ensure you've copied the full API key without any extra spaces
   - Check if your API key has expired or been revoked
   - Generate a new API key if necessary

2. **Connection Issues**:
   - Verify your internet connection
   - Check if there are any Pinecone service outages
   - Ensure your firewall isn't blocking connections to Pinecone

3. **Index Not Found**:
   - Double-check the index name and environment
   - Ensure you're using the correct host URL for your index

4. **Rate Limiting**:
   - Free tier accounts have usage limits
   - If you're hitting rate limits, consider optimizing your queries or upgrading your plan

## Additional Resources

- [Pinecone Documentation](https://docs.pinecone.io/)
- [Pinecone API Reference](https://docs.pinecone.io/reference)
- [Pinecone Pricing](https://www.pinecone.io/pricing/)
- [Pinecone Support](https://support.pinecone.io/)

## Next Steps

After successfully setting up your Pinecone account and obtaining your API key, return to the [Setup and Configuration](../setup_and_configuration.md) guide to continue setting up DprgArchiveAgent. 