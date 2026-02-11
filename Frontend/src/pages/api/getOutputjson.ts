import { getApiHeaders } from '../../utils/api';
import { API_BASE_URL, API_ENDPOINTS } from '../../constants/api';

export const createOutputJsonApi = {
    getOutputJson: async (filters: { inputJson: string }): Promise<any> => {
        const headers = await getApiHeaders();
    
        // Build query parameters
        const params = new URLSearchParams();
        if (filters.inputJson) params.append('inputJson', filters.inputJson);
        const url = `${API_BASE_URL}${API_ENDPOINTS.GET_OUTPUT_JSON}${params.toString() ? `?${params.toString()}` : ''}`;
        const response = await fetch(url, {
          method: 'GET',
          headers
        });
    
        if (!response.ok) {
          return null;
        }
        const result = await response.json();
        if (result.status === 'failure') {
          return null;
        }
        return result || [];
    }
}
