import { fetchAuthSession } from 'aws-amplify/auth';

/**
 * Get authentication token from AWS Amplify
 */
export const getAuthToken = async (): Promise<string | null> => {
  try {
    const session = await fetchAuthSession();
    return session.tokens?.idToken?.toString() || null;
  } catch (error) {
    console.error('Failed to get auth token:', error);
    return null;
  }
};

/**
 * Generate common headers for API requests including authentication
 */
export const getApiHeaders = async (): Promise<HeadersInit> => {
  const token = await getAuthToken();
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  return headers;
};