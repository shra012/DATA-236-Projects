import { useMemo } from 'react';

export default function usePagination(total = 0, page = 1, perPage = 9) {
  const totalPages = useMemo(() => Math.max(1, Math.ceil(total / perPage)), [total, perPage]);
  const skip = (page - 1) * perPage;
  return { totalPages, skip };
}
