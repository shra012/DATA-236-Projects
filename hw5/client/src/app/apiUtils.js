// Small helper utilities used by client API calls
export function handleApiError(error) {
  return error?.response?.data?.detail || error?.message || 'Request failed';
}

export function buildPaginationParams(page = 1, perPage = 10) {
  const limit = perPage;
  const skip = (page - 1) * perPage;
  return { skip, limit };
}
