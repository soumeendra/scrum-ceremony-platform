'use client';

import * as React from 'react';
import { Toaster } from 'sonner';

export function ToastProvider({ children }: { children: React.ReactNode }) {
  return (
    <>
      {children}
      <Toaster
        position="bottom-right"
        toastOptions={{
          classNames: {
            toast:
              'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700',
            title: 'text-slate-900 dark:text-slate-100',
            description: 'text-slate-600 dark:text-slate-400',
          },
        }}
      />
    </>
  );
}
