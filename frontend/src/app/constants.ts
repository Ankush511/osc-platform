import {
  Sparkles,
  Trophy,
  TrendingUp,
  Zap,
  Users,
  Award,
  Github,
  Target,
  GitPullRequest,
  CheckCircle2,
  Star,
  type LucideIcon,
} from "lucide-react";

// ─── Types ──────────────────────────────────────────────────────────────────
export interface Feature {
  title: string;
  description: string;
  icon: LucideIcon;
}

export interface Step {
  title: string;
  description: string;
  icon: LucideIcon;
}

export interface Testimonial {
  quote: string;
  name: string;
  title: string;
}

export interface Stat {
  value: string;
  label: string;
  icon: LucideIcon;
}

// ─── IDE Lines ──────────────────────────────────────────────────────────────
export const IDE_LINES = [
  "🔍 Analyzing your GitHub profile...",
  "",
  "✅ Found 3 matching repositories:",
  "   • react (facebook) — 12 good-first-issues",
  "   • next.js (vercel) — 8 beginner-friendly",
  "   • typescript (microsoft) — 5 help-wanted",
  "",
  "🤖 AI Recommendation:",
  "   Based on your React & TypeScript skills,",
  "   Issue #4821 in next.js is a perfect match.",
  "",
  "   Difficulty: ⭐ Easy",
  "   Est. Time: ~2 hours",
  "   Skills: React, TypeScript",
  "",
  "🚀 Ready to contribute! Claim this issue →",
];

// ─── Stats ──────────────────────────────────────────────────────────────────
export const STATS: Stat[] = [
  { value: "1.2K+", label: "Active Contributors", icon: Users },
  { value: "3000+", label: "Open Issues", icon: CheckCircle2 },
  { value: "300+", label: "Open Source Projects", icon: Star },
];

// ─── Features ───────────────────────────────────────────────────────────────
export const FEATURES: Feature[] = [
  {
    title: "AI-Powered Matching",
    description: "Our intelligent system analyzes your skills and matches you with perfect issues tailored to your experience level.",
    icon: Sparkles,
  },
  {
    title: "Gamification",
    description: "Earn points, unlock achievements, and climb leaderboards as you contribute to open source projects.",
    icon: Trophy,
  },
  {
    title: "Real-time Analytics",
    description: "Track your contributions, PRs, and impact with comprehensive analytics and beautiful visualizations.",
    icon: TrendingUp,
  },
  {
    title: "Beginner Friendly",
    description: "Curated issues perfect for first-time contributors with detailed guidance and mentorship.",
    icon: Zap,
  },
  {
    title: "Community Support",
    description: "Join a thriving community of developers helping each other grow and succeed in open source.",
    icon: Users,
  },
  {
    title: "Achievement System",
    description: "Showcase your progress with badges and achievements that highlight your open source journey.",
    icon: Award,
  },
];

// ─── Steps ──────────────────────────────────────────────────────────────────
export const STEPS: Step[] = [
  {
    title: "Sign In with GitHub",
    description: "Connect your GitHub account securely. We'll analyze your profile to understand your skills and interests.",
    icon: Github,
  },
  {
    title: "Discover Issues",
    description: "Browse AI-curated beginner-friendly issues from top open source projects that match your profile.",
    icon: Target,
  },
  {
    title: "Contribute & Learn",
    description: "Claim an issue, get AI guidance and code suggestions, then submit your pull request with confidence.",
    icon: GitPullRequest,
  },
  {
    title: "Earn Rewards",
    description: "Get points, unlock achievements, climb leaderboards, and showcase your open source contributions.",
    icon: Trophy,
  },
];

// ─── Testimonials ───────────────────────────────────────────────────────────
export const TESTIMONIALS: Testimonial[] = [
  {
    quote: "Contributors.in made my first open source contribution incredibly easy! The AI recommendations were spot-on.",
    name: "Priya Sharma",
    title: "Software Engineer at Google",
  },
  {
    quote: "I went from zero to 50+ PRs in 3 months. The gamification keeps me motivated and the community is amazing.",
    name: "Rahul Verma",
    title: "Full Stack Developer",
  },
  {
    quote: "As a beginner, I was intimidated by open source. This platform gave me the confidence I needed to start.",
    name: "Ananya Patel",
    title: "Junior Developer",
  },
  {
    quote: "The AI-powered issue matching is incredible. It understands my skill level perfectly.",
    name: "Arjun Reddy",
    title: "Frontend Developer",
  },
  {
    quote: "I love the achievement system! Contributing to open source has never been this fun and rewarding.",
    name: "Sneha Gupta",
    title: "CS Student at IIT Delhi",
  },
  {
    quote: "This platform transformed my career. From college student to landing my dream job through open source.",
    name: "Vikram Singh",
    title: "DevOps Engineer at Microsoft",
  },
];

// ─── First Names (180 for signup toasts) ────────────────────────────────────
export const FIRST_NAMES = [
  "Aarav","Aditi","Aisha","Ajay","Akash","Amit","Ananya","Anil","Anjali","Arjun",
  "Aryan","Bhavna","Chetan","Deepa","Deepak","Devi","Dhruv","Divya","Esha","Gaurav",
  "Geeta","Harsh","Isha","Ishaan","Jaya","Kabir","Karan","Kavya","Kiara","Krish",
  "Lakshmi","Manish","Maya","Meera","Mohit","Naina","Nakul","Neha","Nikhil","Nisha",
  "Omkar","Pallavi","Pankaj","Pooja","Prachi","Pranav","Priya","Rahul","Raj","Rajesh",
  "Ravi","Rekha","Rishi","Ritika","Rohit","Rohan","Ruchi","Sachin","Sahil","Sakshi",
  "Samar","Sandeep","Sanjay","Sapna","Sarika","Saurabh","Shikha","Shivam","Shreya","Siddharth",
  "Simran","Sneha","Sonal","Sunil","Sunita","Suresh","Swati","Tanvi","Tarun","Tina",
  "Tushar","Uma","Varun","Vidya","Vijay","Vikram","Vinay","Vinod","Vivek","Yash",
  "Aditya","Alok","Amrita","Ankita","Ashish","Bharat","Chandra","Daksh","Ekta","Farhan",
  "Gauri","Hemant","Indira","Jatin","Kiran","Lalit","Madhav","Nandini","Ojas","Padma",
  "Qadir","Ramesh","Seema","Tanmay","Uday","Vandana","Wasim","Yashika","Zara","Arun",
  "Bala","Charu","Darshan","Ela","Firoz","Gita","Hari","Ira","Jai","Kamala",
  "Lata","Madan","Naren","Om","Prem","Radha","Sagar","Tara","Usha","Veena",
  "Waris","Yamini","Zubin","Abhi","Bindu","Chirag","Disha","Eshan","Falguni","Girish",
  "Hema","Ishan","Jyoti","Kunal","Leela","Mira","Naveen","Omi","Pari","Reena",
  "Suman","Trilok","Urvi","Vimal","Wahid","Yuvraj","Zoya","Aman","Bhavesh","Chhavi",
  "Dev","Eesha","Fatima","Gopal","Hina","Indu","Jagat","Komal","Laxman","Mukesh",
];

// ─── Footer Links ───────────────────────────────────────────────────────────
export const PLATFORM_LINKS = [
  { name: "Browse Issues", href: "/issues" },
  { name: "Dashboard", href: "/dashboard" },
  { name: "Leaderboard", href: "/leaderboard" },
  { name: "Achievements", href: "/achievements" },
];

export const RESOURCE_LINKS = [
  { name: "About Us", href: "/about" },
  { name: "Our Vision", href: "/vision" },
  { name: "Our Mission", href: "/mission" },
  { name: "Community", href: "/community" },
];

// ─── Nav Links ──────────────────────────────────────────────────────────────
export const NAV_LINKS = [
  { label: "Features", id: "features" },
  { label: "How It Works", id: "how-it-works" },
  { label: "Community", id: "community" },
];
