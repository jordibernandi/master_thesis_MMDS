import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 transition duration-300 ease-in-out",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-primary text-primary-foreground shadow",
        secondary:
          "border-transparent bg-secondary text-secondary-foreground",
        destructive:
          "border-transparent bg-destructive text-destructive-foreground shadow hover:bg-destructive/80",
        outline: "text-foreground hover:bg-primary/80 hover:text-primary-foreground",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
  VariantProps<typeof badgeVariants> {
  onClose?: () => void; // Function to be called when close button is clicked
  closable?: boolean; // Optional prop to determine if the close button should be rendered
}

function Badge({ className, variant, onClose, closable = false, children, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props}>
      {children}
      {closable && (
        <button
          type="button"
          className="ml-2 text-xs font-medium text-gray-500 hover:text-red-600 focus:outline-none"
          onClick={onClose}
        >
          &#10006; {/* This is the "X" character */}
        </button>
      )}
    </div>
  )
}

export { Badge, badgeVariants }
