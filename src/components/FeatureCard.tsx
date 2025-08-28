import { cn } from "@/lib/utils";

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  className?: string;
}

export const FeatureCard = ({ icon, title, description, className }: FeatureCardProps) => {
  return (
    <div className={cn(
      "bg-card rounded-2xl p-8 border border-border/50 hover-float",
      "backdrop-blur-sm bg-gradient-to-br from-card/80 to-card/40",
      "transition-all duration-300 cursor-pointer",
      className
    )}>
      <div className="flex flex-col items-center text-center space-y-4">
        <div className="p-4 rounded-xl bg-primary/10 text-primary animate-glow">
          {icon}
        </div>
        <h3 className="text-xl font-semibold text-foreground">
          {title}
        </h3>
        <p className="text-muted-foreground leading-relaxed">
          {description}
        </p>
      </div>
    </div>
  );
};