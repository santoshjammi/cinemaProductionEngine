import * as React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  'inline-flex items-center justify-center whitespace-nowrap font-body transition-transform active:scale-95 focus-visible:outline-2 focus-visible:outline-primary-focus disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground rounded-pill text-body px-[22px] py-[11px]',
        destructive: 'bg-destructive text-destructive-foreground rounded-pill text-body px-[22px] py-[11px]',
        outline: 'bg-transparent text-primary border border-primary rounded-pill text-body px-[22px] py-[11px]',
        secondary: 'bg-ink text-body-on-dark rounded-sm text-caption px-[15px] py-[8px]',
        ghost: 'bg-surface-pearl text-ink-muted-80 rounded-md text-caption px-[14px] py-[8px] border-3 border-divider-soft',
        link: 'text-primary hover:underline',
      },
      size: {
        default: '',
        sm: 'text-caption px-[14px] py-[8px]',
        lg: 'text-body px-[28px] py-[14px]',
        icon: 'w-[44px] h-[44px] rounded-full bg-surface-chip-translucent/64',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button';
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = 'Button';

export { Button, buttonVariants };
