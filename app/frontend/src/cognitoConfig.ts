// AWS Cognito config for the frontend (no backend changes).
// Values come from Vite env so you can plug your real pool later.
export const cognitoConfig = {
  region: import.meta.env.VITE_COGNITO_REGION as string | undefined,
  userPoolId: import.meta.env.VITE_COGNITO_USER_POOL_ID as string | undefined,
  userPoolWebClientId: import.meta.env.VITE_COGNITO_USER_POOL_CLIENT_ID as string | undefined,
}

export const isCognitoConfigured =
  !!cognitoConfig.region && !!cognitoConfig.userPoolId && !!cognitoConfig.userPoolWebClientId

