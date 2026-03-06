import { cognitoConfig, isCognitoConfigured } from './cognitoConfig'

function getAuthority(): string {
  if (import.meta.env.VITE_COGNITO_AUTHORITY) return import.meta.env.VITE_COGNITO_AUTHORITY
  if (isCognitoConfigured && cognitoConfig.region && cognitoConfig.userPoolId)
    return `https://cognito-idp.${cognitoConfig.region}.amazonaws.com/${cognitoConfig.userPoolId}`
  return 'https://cognito-idp.ap-south-1.amazonaws.com/ap-south-1_g1M7FbU0x'
}

export const oidcConfig = {
  authority: getAuthority(),
  client_id:
    import.meta.env.VITE_COGNITO_CLIENT_ID ||
    (isCognitoConfigured ? cognitoConfig.userPoolWebClientId : '') ||
    '3aiio9gu0q1j55luime7o03k5j',
  redirect_uri:
    import.meta.env.VITE_COGNITO_REDIRECT_URI || 'http://localhost:5173',
  response_type: 'code',
  scope: 'openid phone email',
}

