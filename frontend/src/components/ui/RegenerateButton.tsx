import React from 'react';
import { Button, type ButtonProps } from './Button';
import { cn } from '@/lib/utils';

interface RegenerateButtonProps extends Omit<ButtonProps, 'children'> {
  isLoading?: boolean;
}

export function RegenerateButton({
  isLoading,
  disabled,
  className,
  ...props
}: RegenerateButtonProps) {
  return (
    <Button
      variant="outline"
      size="sm"
      disabled={disabled || isLoading}
      className={cn('gap-2', className)}
      {...props}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="14"
        height="14"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className={cn(isLoading && 'animate-spin')}
      >
        <path d="M21 12a9 9 0 1 1-6.219-8.56" />
      </svg>
      {isLoading ? 'Regenerating...' : 'Regenerate'}
    </Button>
  );
}
