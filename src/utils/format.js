export function formatETB(value) {
  const amount = Number(value) || 0;
  try {
    return new Intl.NumberFormat('en-ET', {
      style: 'currency',
      currency: 'ETB',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount);
  } catch (_) {
    return `ETB ${amount.toFixed(2)}`;
  }
}


