import React from 'react';
import VercelAnalytics from '../components/VercelAnalytics';

// Default implementation, that you can customize
export default function Root({children}): JSX.Element {
  return (
    <>
      {children}
      <VercelAnalytics />
    </>
  );
}
