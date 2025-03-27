# Setting Up OpenAI

DprgArchiveAgent uses OpenAI API for generating embeddings from text. This guide walks you through setting up an OpenAI account and obtaining an API key.

## What is OpenAI?

[OpenAI](https://openai.com/) is an AI research and deployment company that provides various AI models and services. DprgArchiveAgent uses OpenAI's embedding models to convert text into vector representations for semantic search.

## Creating an OpenAI Account

1. **Visit the OpenAI website**:
   - Go to [https://openai.com/](https://openai.com/)
   - Click on "Sign Up" or navigate to [https://platform.openai.com/signup](https://platform.openai.com/signup)

2. **Sign up for an account**:
   - You can sign up using:
     - Email and password
     - Google account
     - Microsoft account
     - Apple account
   - Follow the on-screen instructions to complete the signup process

3. **Verify your email** (if required):
   - Check your inbox for a verification email from OpenAI
   - Click the verification link to confirm your account

4. **Provide phone number verification**:
   - OpenAI requires phone verification for new accounts
   - Enter your phone number in the format requested
   - Enter the verification code sent to your phone

## Subscription Options

OpenAI offers different subscription tiers:

1. **Free Tier**:
   - Limited usage (currently approximately $5 of free credits for new accounts)
   - Rate limits apply
   - Access to most models

2. **Pay-as-you-go**:
   - Pay only for what you use
   - Higher rate limits than free tier
   - Requires adding a payment method

3. **Prepaid plans**:
   - Purchase credits in advance
   - Good for predictable budgeting

For DprgArchiveAgent's embedding usage, the free tier or pay-as-you-go with a usage cap should be suitable for most users.

## Getting Your API Key

1. **Log in to your OpenAI account**:
   - Go to [https://platform.openai.com/](https://platform.openai.com/)
   - Sign in with your credentials

2. **Navigate to API Keys**:
   - Click on your account icon in the top-right corner
   - Select "View API keys" or go directly to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)

3. **Create a new API Key**:
   - Click on "Create new secret key"
   - You can provide a name for your key (e.g., "DprgArchiveAgent")
   - Click "Create secret key"

4. **Copy your API Key**:
   - Your new API key will be displayed only once
   - Copy this key immediately and store it securely
   - Note: You cannot view the full key again after closing the window, only create new ones

## Setting Up Billing (Optional for Testing)

If you plan to use the API beyond the free tier limits:

1. **Navigate to Billing Settings**:
   - Click on your account icon
   - Select "Billing" or go to [https://platform.openai.com/account/billing/overview](https://platform.openai.com/account/billing/overview)

2. **Add a Payment Method**:
   - Click "Add payment method"
   - Enter your credit card or other payment details
   - Follow the prompts to complete setup

3. **Set Usage Limits** (Recommended):
   - Go to "Usage limits" under Billing
   - Set a hard cap on your monthly spending
   - This prevents unexpected charges if your application makes more requests than anticipated

## Setting Up for DprgArchiveAgent

For DprgArchiveAgent, you'll need:
- Your OpenAI API Key

This value will be added to your `.env` file when configuring the application.

### Example Configuration

In your `.env` file, you'll add:

```
OPENAI_API_KEY=your_api_key_here
```

By default, the application uses the `text-embedding-3-large` model, which offers a good balance of performance and cost. You can override this by setting:

```
EMBEDDING_MODEL=text-embedding-3-small  # For a smaller, faster model
```

## Understanding Costs

For embeddings, OpenAI charges based on the number of tokens processed:

- `text-embedding-3-large`: $0.00013 / 1K tokens
- `text-embedding-3-small`: $0.00002 / 1K tokens

A token is approximately 4 characters or 0.75 words in English text.

For typical usage in DprgArchiveAgent, costs are usually minimal, as:
- Embeddings are only generated for search queries
- The application efficiently manages token usage

## API Usage and Best Practices

1. **Keep your API key secure**:
   - Do not share your API key or commit it to public repositories
   - Use environment variables or secure storage methods
   - Rotate keys periodically for enhanced security

2. **Monitor your usage**:
   - Regularly check your usage in the OpenAI dashboard
   - Set up usage alerts if available
   - Implement rate limiting in your application if needed

3. **Handle errors gracefully**:
   - Implement proper error handling for API rate limits and other issues
   - Add retries with exponential backoff for transient errors

## Troubleshooting

### Common Issues

1. **API Key Not Working**:
   - Ensure you've copied the full API key without any extra spaces
   - Check if your API key has expired or been revoked
   - Verify your account is in good standing (no payment issues)
   - Create a new API key if necessary

2. **Rate Limit Errors**:
   - Free tier and new accounts have stricter rate limits
   - Implement request throttling or reduce parallel requests
   - Consider upgrading to a paid tier for higher limits

3. **Billing Issues**:
   - Ensure your payment method is valid and up to date
   - Check if you've reached your usage cap
   - Verify there are no restrictions on your account

## Additional Resources

- [OpenAI API Documentation](https://platform.openai.com/docs/introduction)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [OpenAI Pricing](https://openai.com/pricing)
- [OpenAI Help Center](https://help.openai.com/)

## Next Steps

After successfully setting up your OpenAI account and obtaining your API key, return to the [Setup and Configuration](../setup_and_configuration.md) guide to continue setting up DprgArchiveAgent. 