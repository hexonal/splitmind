import { motion } from 'framer-motion';
import { 
  Github, 
  ExternalLink, 
  Heart, 
  Brain, 
  Cpu,
  Globe,
  Mail,
  Twitter,
  Linkedin,
  Code
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

export function GlobalFooter() {
  const currentYear = new Date().getFullYear();
  
  const socialLinks = [
    {
      name: 'GitHub',
      icon: Github,
      href: 'https://github.com/webdevtodayjason',
      color: 'hover:text-gray-300'
    },
    {
      name: 'Twitter',
      icon: Twitter,
      href: 'https://twitter.com/webdevtodayjason',
      color: 'hover:text-blue-400'
    },
    {
      name: 'LinkedIn',
      icon: Linkedin,
      href: 'https://linkedin.com/in/jasonbrashear',
      color: 'hover:text-blue-600'
    },
    {
      name: 'Website',
      icon: Globe,
      href: 'https://webdevtoday.com',
      color: 'hover:text-green-400'
    }
  ];

  const quickLinks = [
    { name: 'Documentation', href: 'https://github.com/webdevtodayjason/splitmind/docs' },
    { name: 'API Reference', href: 'https://github.com/webdevtodayjason/splitmind/api' },
    { name: 'Tutorials', href: 'https://github.com/webdevtodayjason/splitmind/tutorials' },
    { name: 'Roadmap', href: 'https://github.com/webdevtodayjason/splitmind/roadmap' }
  ];

  const features = [
    { name: 'Multi-Agent AI', icon: Brain },
    { name: 'Real-time Coordination', icon: Cpu },
    { name: 'Git Integration', icon: Code },
    { name: 'Task Orchestration', icon: ExternalLink }
  ];

  return (
    <motion.footer 
      className="relative mt-auto border-t border-electric-cyan/20 bg-dark-bg/95 backdrop-blur-sm"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-grid-pattern bg-[length:32px_32px] opacity-5" />
      
      <div className="relative container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          
          {/* Brand Section */}
          <div className="md:col-span-1">
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-electric-cyan to-blue-500 rounded-lg flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-electric-cyan to-white bg-clip-text text-transparent">
                SplitMind
              </span>
              <Badge variant="outline" className="text-xs border-electric-cyan/20 text-electric-cyan">
                v2.0
              </Badge>
            </div>
            <p className="text-muted-foreground text-sm leading-relaxed mb-4">
              AI-powered multi-agent development orchestration platform. 
              Built for developers who think bigger.
            </p>
            <div className="flex items-center space-x-1 text-sm text-muted-foreground">
              <span>Made with</span>
              <Heart className="w-4 h-4 text-red-500 mx-1" />
              <span>by</span>
              <a 
                href="https://webdevtoday.com" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-electric-cyan hover:underline ml-1"
              >
                Jason Brashear
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div className="md:col-span-1">
            <h4 className="text-sm font-semibold text-white mb-4">Resources</h4>
            <ul className="space-y-2">
              {quickLinks.map((link) => (
                <li key={link.name}>
                  <a
                    href={link.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-muted-foreground hover:text-electric-cyan transition-colors flex items-center group"
                  >
                    {link.name}
                    <ExternalLink className="w-3 h-3 ml-1 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Features */}
          <div className="md:col-span-1">
            <h4 className="text-sm font-semibold text-white mb-4">Key Features</h4>
            <ul className="space-y-2">
              {features.map((feature) => (
                <li key={feature.name} className="flex items-center space-x-2">
                  <feature.icon className="w-4 h-4 text-electric-cyan" />
                  <span className="text-sm text-muted-foreground">{feature.name}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Social & Tech Stack */}
          <div className="md:col-span-1">
            <h4 className="text-sm font-semibold text-white mb-4">Connect</h4>
            <div className="flex items-center space-x-2 mb-6">
              {socialLinks.map((social) => (
                <Button
                  key={social.name}
                  variant="ghost"
                  size="sm"
                  asChild
                  className={`p-2 h-8 w-8 ${social.color} transition-colors`}
                >
                  <a
                    href={social.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    title={social.name}
                  >
                    <social.icon className="w-4 h-4" />
                  </a>
                </Button>
              ))}
            </div>
            
            <div className="space-y-2">
              <h5 className="text-xs font-medium text-muted-foreground">Built with</h5>
              <div className="flex flex-wrap gap-1">
                <Badge variant="secondary" className="text-xs">React</Badge>
                <Badge variant="secondary" className="text-xs">TypeScript</Badge>
                <Badge variant="secondary" className="text-xs">FastAPI</Badge>
                <Badge variant="secondary" className="text-xs">Python</Badge>
                <Badge variant="secondary" className="text-xs">Claude AI</Badge>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-electric-cyan/10 mt-8 pt-6">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            
            {/* Copyright */}
            <div className="text-sm text-muted-foreground">
              © {currentYear} SplitMind. All rights reserved.
            </div>

            {/* Status & Links */}
            <div className="flex items-center space-x-6 text-sm">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-muted-foreground">All systems operational</span>
              </div>
              
              <a 
                href="mailto:jason@webdevtoday.com" 
                className="text-muted-foreground hover:text-electric-cyan transition-colors flex items-center space-x-1"
              >
                <Mail className="w-4 h-4" />
                <span>Support</span>
              </a>
              
              <a 
                href="https://github.com/webdevtodayjason/splitmind/issues" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-muted-foreground hover:text-electric-cyan transition-colors flex items-center space-x-1"
              >
                <Github className="w-4 h-4" />
                <span>Issues</span>
              </a>
            </div>
          </div>
        </div>
      </div>
    </motion.footer>
  );
}