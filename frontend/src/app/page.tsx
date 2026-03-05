"use client";

import Link from "next/link";
import dynamic from "next/dynamic";
import { motion, useScroll, useTransform, useSpring, AnimatePresence } from "framer-motion";
import { useRef, useState, useEffect, useCallback } from "react";
import { LogoIcon } from "@/components/ui/Logo"
import {
  Github,
  Sparkles,
  ArrowRight,
  Star,
  Rocket,
  Target,
  ChevronDown,
  Terminal,
  UserPlus,
} from "lucide-react";

const AuthNavButton = dynamic(() => import("@/components/AuthNavButton").then(m => m.AuthNavButton), { ssr: false, loading: () => <div className="w-[120px] h-[40px] rounded-xl bg-white/5 animate-pulse" /> });
const AuthCTAButton = dynamic(() => import("@/components/AuthNavButton").then(m => m.AuthCTAButton), { ssr: false, loading: () => <div className="w-[280px] h-[56px] rounded-2xl bg-white/5 animate-pulse" /> });
import {
  IDE_LINES,
  STATS,
  FEATURES,
  STEPS,
  TESTIMONIALS,
  FIRST_NAMES,
  NAV_LINKS,
  PLATFORM_LINKS,
  RESOURCE_LINKS,
} from "./constants";

// ─── Typing IDE Component ───────────────────────────────────────────────────
function TypingIDE() {
  const [displayedText, setDisplayedText] = useState("");
  const [lineIndex, setLineIndex] = useState(0);
  const [charIndex, setCharIndex] = useState(0);
  const [showCursor, setShowCursor] = useState(true);

  useEffect(() => {
    const cursorInterval = setInterval(() => setShowCursor((p) => !p), 530);
    return () => clearInterval(cursorInterval);
  }, []);

  useEffect(() => {
    if (lineIndex >= IDE_LINES.length) return;
    const currentLine = IDE_LINES[lineIndex];

    if (charIndex <= currentLine.length) {
      const timeout = setTimeout(() => {
        setDisplayedText((prev) => {
          const allLines = prev.split("\n");
          allLines[lineIndex] = currentLine.slice(0, charIndex);
          return allLines.join("\n");
        });
        setCharIndex((c) => c + 1);
      }, currentLine === "" ? 100 : 28);
      return () => clearTimeout(timeout);
    }

    const nextTimeout = setTimeout(() => {
      setDisplayedText((prev) => prev + "\n");
      setLineIndex((l) => l + 1);
      setCharIndex(0);
    }, 300);
    return () => clearTimeout(nextTimeout);
  }, [lineIndex, charIndex]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.8, duration: 0.7 }}
      className="relative max-w-2xl mx-auto"
    >
      <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 rounded-2xl blur-2xl" />
      <div className="relative bg-[#0d1117] border border-white/10 rounded-2xl overflow-hidden shadow-2xl shadow-cyan-500/10">
        <div className="flex items-center justify-between px-4 py-3 bg-[#161b22] border-b border-white/5">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-[#ff5f57]" />
            <div className="w-3 h-3 rounded-full bg-[#febc2e]" />
            <div className="w-3 h-3 rounded-full bg-[#28c840]" />
          </div>
          <div className="flex items-center space-x-2 text-gray-400 text-xs">
            <Terminal className="h-3.5 w-3.5" />
            <span className="font-mono">contributors.in — AI Assistant</span>
          </div>
          <div className="w-14" />
        </div>
        <div className="p-5 h-[340px] overflow-hidden">
          <pre className="font-mono text-sm leading-relaxed whitespace-pre-wrap text-gray-300">
            {displayedText}
            {lineIndex < IDE_LINES.length && (
              <span className={`inline-block w-2 h-4 -mb-0.5 bg-cyan-400 ${showCursor ? "opacity-100" : "opacity-0"}`} />
            )}
          </pre>
        </div>
      </div>
    </motion.div>
  );
}

// ─── User Signup Toast ──────────────────────────────────────────────────────
interface ToastData {
  id: number;
  name: string;
}

function SignupToasts() {
  const [toasts, setToasts] = useState<ToastData[]>([]);
  const counterRef = useRef(0);

  const addToast = useCallback(() => {
    const name = FIRST_NAMES[Math.floor(Math.random() * FIRST_NAMES.length)];
    const id = counterRef.current++;
    setToasts((prev) => [...prev.slice(-2), { id, name }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  }, []);

  useEffect(() => {
    const initialDelay = setTimeout(() => {
      addToast();
      const scheduleNext = () => {
        const delay = 8000 + Math.random() * 6000; // 8–14 seconds
        return setTimeout(() => {
          addToast();
          timerRef = scheduleNext();
        }, delay);
      };
      let timerRef = scheduleNext();
      return () => clearTimeout(timerRef);
    }, 5000);
    return () => clearTimeout(initialDelay);
  }, [addToast]);

  return (
    <div className="fixed bottom-6 left-6 z-50 flex flex-col space-y-3 pointer-events-none">
      <AnimatePresence mode="popLayout">
        {toasts.map((toast) => (
          <motion.div
            key={toast.id}
            initial={{ opacity: 0, x: -80, scale: 0.8 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: -80, scale: 0.8 }}
            transition={{ type: "spring", stiffness: 300, damping: 25 }}
            className="pointer-events-auto flex items-center space-x-3 px-5 py-3 rounded-xl bg-[#0d1117]/90 backdrop-blur-xl border border-cyan-500/20 shadow-lg shadow-cyan-500/10"
          >
            <div className="flex items-center justify-center w-9 h-9 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 text-white text-sm font-bold shrink-0">
              {toast.name.charAt(0)}
            </div>
            <div className="min-w-0">
              <p className="text-white text-sm font-semibold truncate">{toast.name} just signed up</p>
              <p className="text-gray-400 text-xs">a few seconds ago</p>
            </div>
            <UserPlus className="h-4 w-4 text-cyan-400 shrink-0" />
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}

// ─── Floating Particles ─────────────────────────────────────────────────────
function FloatingParticles() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  if (!mounted) return <div className="absolute inset-0 overflow-hidden pointer-events-none" />;

  // Generate stable random values only on the client to avoid hydration mismatch
  const particles = Array.from({ length: 20 }).map((_, i) => ({
    id: i,
    ix: `${Math.random() * 100}%`,
    iy: `${Math.random() * 100}%`,
    ax: [`${Math.random() * 100}%`, `${Math.random() * 100}%`],
    ay: [`${Math.random() * 100}%`, `${Math.random() * 100}%`],
    dur: 8 + Math.random() * 12,
    del: Math.random() * 5,
  }));

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {particles.map((p) => (
        <motion.div
          key={p.id}
          className="absolute w-1 h-1 rounded-full bg-cyan-400/30"
          initial={{ x: p.ix, y: p.iy, opacity: 0 }}
          animate={{ y: p.ay, x: p.ax, opacity: [0, 0.6, 0] }}
          transition={{ duration: p.dur, repeat: Infinity, delay: p.del, ease: "linear" }}
        />
      ))}
    </div>
  );
}

// ─── Main Page ──────────────────────────────────────────────────────────────
export default function Home() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end start"],
  });

  const y = useTransform(scrollYProgress, [0, 1], ["0%", "50%"]);
  const opacity = useTransform(scrollYProgress, [0, 0.5, 1], [1, 0.5, 0]);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  const springConfig = { stiffness: 150, damping: 15 };
  const mouseX = useSpring(mousePosition.x, springConfig);
  const mouseY = useSpring(mousePosition.y, springConfig);

  return (
    <div ref={containerRef} className="relative min-h-screen bg-black overflow-hidden">
      <SignupToasts />

      {/* Animated Background Grid */}
      <div className="fixed inset-0 z-0">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a_1px,transparent_1px),linear-gradient(to_bottom,#0f172a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_0%,#000_70%,transparent_110%)]" />
        <motion.div
          className="absolute inset-0 opacity-30"
          style={{
            background: `radial-gradient(600px circle at ${mouseX}px ${mouseY}px, rgba(6, 182, 212, 0.15), transparent 40%)`,
          }}
        />
      </div>

      {/* Navigation */}
      <motion.nav
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="fixed top-0 w-full z-50 border-b border-white/5 bg-black/50 backdrop-blur-2xl"
      >
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            <Link href="/" className="flex items-center space-x-3 group">
              <motion.div whileHover={{ scale: 1.05, rotate: 5 }} className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-2xl blur-xl opacity-50 group-hover:opacity-75 transition-opacity" />
                <LogoIcon size="md" />
              </motion.div>
              <div>
                <span className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                  Contributors
                </span>
                <span className="text-cyan-400 text-xs font-mono">.in</span>
              </div>
            </Link>

            <div className="hidden md:flex items-center space-x-8">
              {NAV_LINKS.map((item) => (
                <a
                  key={item.id}
                  href={`#${item.id}`}
                  className="text-gray-400 hover:text-white transition-colors text-sm font-medium relative group"
                >
                  {item.label}
                  <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-cyan-400 to-blue-500 group-hover:w-full transition-all duration-300" />
                </a>
              ))}
              <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                <AuthNavButton />
              </motion.div>
            </div>
          </div>
        </div>
      </motion.nav>

      {/* Hero Section */}
      <section className="relative min-h-screen flex flex-col justify-center px-6 pt-32 pb-16">
        <FloatingParticles />
        <motion.div style={{ y, opacity }} className="relative z-10 max-w-7xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="inline-flex items-center space-x-2 px-4 py-2 rounded-full bg-gradient-to-r from-cyan-500/10 to-blue-500/10 border border-cyan-500/20 backdrop-blur-sm mb-8"
          >
            <Sparkles className="h-4 w-4 text-cyan-400 animate-pulse" />
            <span className="text-sm text-cyan-300 font-medium">
              Join 4,000+ developers contributing to open source
            </span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.6 }}
            className="text-5xl sm:text-6xl md:text-8xl font-black mb-8 leading-[1.1]"
          >
            <span className="bg-gradient-to-r from-white via-gray-100 to-gray-300 bg-clip-text text-transparent">
              Your Open Source
            </span>
            <br />
            <motion.span
              className="bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 bg-clip-text text-transparent inline-block"
              animate={{ backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"] }}
              transition={{ duration: 5, repeat: Infinity, ease: "linear" }}
              style={{ backgroundSize: "200% 200%" }}
            >
              Journey Starts Here
            </motion.span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.6 }}
            className="text-lg sm:text-xl md:text-2xl text-gray-400 mb-12 max-w-3xl mx-auto leading-relaxed"
          >
            Discover beginner-friendly issues, get AI-powered guidance, and earn achievements
            while contributing to the world&apos;s best open source projects.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.6 }}
            className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16"
          >
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <AuthCTAButton />
            </motion.div>
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Link
                href="/issues"
                className="inline-flex items-center space-x-2 px-8 py-4 rounded-2xl border-2 border-cyan-500/30 hover:border-cyan-500/60 bg-cyan-500/5 hover:bg-cyan-500/10 transition-all duration-300 text-white font-semibold"
              >
                <Target className="h-5 w-5 text-cyan-400" />
                <span>Explore Issues</span>
              </Link>
            </motion.div>
          </motion.div>

          <TypingIDE />

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1, duration: 0.6 }}
            className="grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-4xl mx-auto mt-16"
          >
            {STATS.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 1.1 + index * 0.1, duration: 0.5 }}
                whileHover={{ scale: 1.05, y: -5 }}
                className="relative group"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <div className="relative bg-gradient-to-br from-white/5 to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-6 hover:border-cyan-500/30 transition-colors">
                  <stat.icon className="h-8 w-8 text-cyan-400 mb-3" />
                  <div className="text-4xl font-black bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent mb-1">
                    {stat.value}
                  </div>
                  <div className="text-gray-400 text-sm font-medium">{stat.label}</div>
                </div>
              </motion.div>
            ))}
          </motion.div>

          {/* Scroll Indicator */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.5, duration: 0.6 }}
            className="mt-16 flex justify-center"
          >
            <motion.div
              animate={{ y: [0, 10, 0] }}
              transition={{ repeat: Infinity, duration: 2 }}
              className="flex flex-col items-center space-y-2 text-gray-500"
            >
              <span className="text-xs font-medium">Scroll to explore</span>
              <ChevronDown className="h-5 w-5" />
            </motion.div>
          </motion.div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section id="features" className="relative py-32 px-6 scroll-mt-24">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-20"
          >
            <span className="text-cyan-400 font-mono text-sm tracking-wider mb-4 block">// POWERFUL FEATURES</span>
            <h2 className="text-5xl md:text-6xl font-black text-white mb-6">
              Everything You Need to{" "}
              <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">Succeed</span>
            </h2>
            <p className="text-gray-400 text-xl max-w-2xl mx-auto">
              Built for developers who want to make their mark in open source
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1, duration: 0.5 }}
                whileHover={{ y: -8, scale: 1.02 }}
                className="group relative"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 to-blue-500/10 rounded-3xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <div className="relative h-full bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-3xl p-8 hover:border-cyan-500/30 transition-all duration-300">
                  <div className="flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-cyan-500/20 to-blue-500/20 mb-6 group-hover:scale-110 transition-transform duration-300">
                    <feature.icon className="h-7 w-7 text-cyan-400" />
                  </div>
                  <h3 className="text-2xl font-bold text-white mb-4 group-hover:text-cyan-400 transition-colors">{feature.title}</h3>
                  <p className="text-gray-400 leading-relaxed">{feature.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="relative py-32 px-6 scroll-mt-24 bg-gradient-to-b from-transparent via-cyan-500/5 to-transparent">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-20"
          >
            <span className="text-cyan-400 font-mono text-sm tracking-wider mb-4 block">// SIMPLE PROCESS</span>
            <h2 className="text-5xl md:text-6xl font-black text-white mb-6">
              Start Contributing in{" "}
              <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">4 Easy Steps</span>
            </h2>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {STEPS.map((step, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.15, duration: 0.5 }}
                className="relative"
              >
                {index < STEPS.length - 1 && (
                  <div className="hidden lg:block absolute top-16 left-full w-full h-0.5 bg-gradient-to-r from-cyan-500/50 to-transparent -translate-x-1/2 z-0" />
                )}
                <motion.div
                  whileHover={{ scale: 1.05, y: -5 }}
                  className="relative z-10 bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-3xl p-8 hover:border-cyan-500/30 transition-all duration-300"
                >
                  <div className="flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-600 text-white font-black text-2xl mb-6 shadow-lg shadow-cyan-500/50">
                    {index + 1}
                  </div>
                  <step.icon className="h-10 w-10 text-cyan-400 mb-4" />
                  <h3 className="text-xl font-bold text-white mb-3">{step.title}</h3>
                  <p className="text-gray-400 text-sm leading-relaxed">{step.description}</p>
                </motion.div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="community" className="relative py-32 px-6 scroll-mt-24">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-20"
          >
            <span className="text-cyan-400 font-mono text-sm tracking-wider mb-4 block">// COMMUNITY LOVE</span>
            <h2 className="text-5xl md:text-6xl font-black text-white mb-6">
              Loved by{" "}
              <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">Developers Worldwide</span>
            </h2>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {TESTIMONIALS.map((testimonial, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1, duration: 0.5 }}
                whileHover={{ y: -5, scale: 1.02 }}
                className="group relative"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 to-blue-500/10 rounded-3xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <div className="relative h-full bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-3xl p-8 hover:border-cyan-500/30 transition-all duration-300">
                  <div className="flex items-center space-x-1 mb-4">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="h-4 w-4 fill-cyan-400 text-cyan-400" />
                    ))}
                  </div>
                  <p className="text-gray-300 leading-relaxed mb-6 italic">
                    &ldquo;{testimonial.quote}&rdquo;
                  </p>
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-white font-bold">
                      {testimonial.name.charAt(0)}
                    </div>
                    <div>
                      <div className="text-white font-semibold">{testimonial.name}</div>
                      <div className="text-gray-400 text-sm">{testimonial.title}</div>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="relative py-32 px-6">
        <div className="max-w-5xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="relative"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 via-blue-500/20 to-purple-500/20 rounded-[3rem] blur-3xl" />
            <div className="relative bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-[3rem] p-12 md:p-16 text-center">
              <motion.div
                initial={{ scale: 0 }}
                whileInView={{ scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 mb-8 shadow-lg shadow-cyan-500/50"
              >
                <Rocket className="h-10 w-10 text-white" />
              </motion.div>

              <h2 className="text-4xl md:text-6xl font-black text-white mb-6 leading-tight">
                Ready to Make Your{" "}
                <span className="bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 bg-clip-text text-transparent">First Contribution?</span>
              </h2>

              <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto">
                Join thousands of developers contributing to open source. Sign in with GitHub and discover your perfect first issue in minutes.
              </p>

              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} className="inline-block">
                <AuthCTAButton size="large" />
              </motion.div>

              <p className="text-gray-500 text-sm mt-6">✨ Free forever • No credit card required • 2 min setup</p>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative border-t border-white/5 py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
            <div className="md:col-span-2">
              <Link href="/" className="flex items-center space-x-3 mb-6 group">
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-2xl blur-xl opacity-50" />
                  <LogoIcon size="md" />
                </div>
                <div>
                  <span className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">Contributors</span>
                  <span className="text-cyan-400 text-xs font-mono">.in</span>
                </div>
              </Link>
              <p className="text-gray-400 text-sm leading-relaxed mb-6 max-w-md">
                Empowering developers to contribute to open source projects with AI-powered guidance, gamification, and a supportive community.
              </p>
              <div className="flex items-center space-x-4">
                <motion.a
                  whileHover={{ scale: 1.1, y: -2 }}
                  href="https://github.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label="Visit our GitHub"
                  className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-gray-400 hover:text-cyan-400 hover:border-cyan-500/50 transition-all"
                >
                  <Github className="h-5 w-5" />
                </motion.a>
              </div>
            </div>

            <div>
              <h3 className="text-white font-bold mb-6">Platform</h3>
              <ul className="space-y-3">
                {PLATFORM_LINKS.map((item) => (
                  <li key={item.name}>
                    <Link href={item.href} className="text-gray-400 hover:text-cyan-400 transition-colors text-sm flex items-center space-x-2 group">
                      <span className="w-0 h-0.5 bg-cyan-400 group-hover:w-4 transition-all duration-300" />
                      <span>{item.name}</span>
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h3 className="text-white font-bold mb-6">Resources</h3>
              <ul className="space-y-3">
                {RESOURCE_LINKS.map((item) => (
                  <li key={item.name}>
                    <Link href={item.href} className="text-gray-400 hover:text-cyan-400 transition-colors text-sm flex items-center space-x-2 group">
                      <span className="w-0 h-0.5 bg-cyan-400 group-hover:w-4 transition-all duration-300" />
                      <span>{item.name}</span>
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="border-t border-white/5 pt-8 flex flex-col md:flex-row justify-between items-center">
            <p className="text-gray-500 text-sm">© 2026 Contributors.in. All rights reserved.</p>
            <div className="flex items-center space-x-6 mt-4 md:mt-0">
              <Link href="/privacy" className="text-gray-500 hover:text-cyan-400 text-sm transition-colors">Privacy</Link>
              <Link href="/terms" className="text-gray-500 hover:text-cyan-400 text-sm transition-colors">Terms</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
