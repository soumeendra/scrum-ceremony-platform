import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const badgeVariants = cva(
  'inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
  {
    variants: {
      variant: {
        default:
          'border-transparent bg-primary-900 text-primary-50 shadow hover:bg-primary-900/80 dark:bg-primary-100 dark:text-primary-900 dark:hover:bg-primary-100/80',
        secondary:
          'border-transparent bg-primary-100 text-primary-900 hover:bg-primary-100/80 dark:bg-primary-800 dark:text-primary-100 dark:hover:bg-primary-800/80',
        success:
          'border-transparent bg-success-100 text-success-700 hover:bg-success-100/80 dark:bg-success-900/30 dark:text-success-300',
        warning:
          'border-transparent bg-warning-100 text-warning-700 hover:bg-warning-100/80 dark:bg-warning-900/30 dark:text-warning-300',
        danger:
          'border-transparent bg-danger-100 text-danger-700 hover:bg-danger-100/80 dark:bg-danger-900/30 dark:text-danger-300',
        accent:
          'border-transparent bg-accent-100 text-accent-700 hover:bg-accent-100/80 dark:bg-accent-900/30 dark:text-accent-300',
        outline: 'text-primary-900 dark:text-primary-100',
        ghost:
          'border-transparent text-primary-700 dark:text-primary-300',
      },
      size: {
        default: 'px-2.5 py-0.5 text-xs',
        sm: 'px-2 py-0.5 text-[10px]',
        lg: 'px-3 py-1 text-sm',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, size, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant, size }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
