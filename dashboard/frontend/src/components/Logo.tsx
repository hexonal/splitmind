import { motion } from 'framer-motion';

export function Logo() {
  return (
    <motion.div 
      className="flex items-center space-x-3"
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
    >
      <img 
        src="/splitmind-logo-200x190.png" 
        alt="SplitMind" 
        className="w-10 h-10 object-contain"
      />
      <div>
        <h1 className="text-xl font-bold bg-gradient-to-r from-electric-cyan to-accent bg-clip-text text-transparent">
          SplitMind
        </h1>
        <p className="text-xs text-muted-foreground -mt-1">Command Center</p>
      </div>
    </motion.div>
  );
}