import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface HeroButtonProps {
  children: React.ReactNode;
  variant?: "primary" | "secondary";
  onClick?: () => void;
  className?: string;
}

export const HeroButton = ({ children, variant = "primary", onClick, className }: HeroButtonProps) => {
  return (
    <Button
      onClick={onClick}
      className={cn(
        "text-lg font-semibold px-8 py-4 rounded-2xl transition-all duration-300 hover:scale-105",
        variant === "primary" 
          ? "bg-primary hover:bg-primary/90 text-primary-foreground glow hover-glow border-0" 
          : "bg-transparent border-2 border-primary text-primary hover:bg-primary hover:text-primary-foreground glow-secondary hover-glow",
        className
      )}
    >
      {children}
    </Button>
  );
};