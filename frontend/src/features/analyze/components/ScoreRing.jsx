import { useEffect, useRef } from 'react';

/**
 * ScoreRing
 * ---------
 * Animated SVG circular progress ring that displays a numeric score.
 *
 * Props:
 *   score     {number}  0-100
 *   label     {string}  text below the ring
 *   color     {string}  stroke color for the ring arc (hex or CSS color)
 *   size      {number}  diameter in px (default 120)
 *   thickness {number}  stroke width in px (default 10)
 */
const ScoreRing = ({ score, label, color = '#3b82f6', size = 120, thickness = 10 }) => {
  const circleRef = useRef(null);
  const radius = (size - thickness) / 2;
  const circumference = 2 * Math.PI * radius;
  const clampedScore = Math.max(0, Math.min(100, score || 0));

  useEffect(() => {
    if (!circleRef.current) return;

    // Start at 0 and animate to the target offset
    circleRef.current.style.strokeDashoffset = circumference.toString();

    const targetOffset = circumference - (clampedScore / 100) * circumference;
    const startTime = performance.now();
    const duration = 1200;

    const animate = (now) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const currentOffset = circumference - eased * (circumference - targetOffset);
      if (circleRef.current) {
        circleRef.current.style.strokeDashoffset = currentOffset.toString();
      }
      if (progress < 1) requestAnimationFrame(animate);
    };

    const frame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frame);
  }, [clampedScore, circumference]);

  const getScoreGrade = (s) => {
    if (s >= 80) return { grade: 'Excellent', textColor: '#22c55e' };
    if (s >= 65) return { grade: 'Good', textColor: '#3b82f6' };
    if (s >= 45) return { grade: 'Average', textColor: '#f59e0b' };
    return { grade: 'Needs Work', textColor: '#ef4444' };
  };

  const { grade, textColor } = getScoreGrade(clampedScore);

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
          {/* Background track */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="#e5e7eb"
            strokeWidth={thickness}
          />
          {/* Animated progress arc */}
          <circle
            ref={circleRef}
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={thickness}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={circumference}
            style={{ transition: 'stroke-dashoffset 0.05s linear' }}
          />
        </svg>

        {/* Center label */}
        <div
          className="absolute inset-0 flex flex-col items-center justify-center"
          style={{ fontSize: size * 0.22, fontWeight: 800, color: textColor }}
        >
          <span>{clampedScore}</span>
          <span style={{ fontSize: size * 0.11, fontWeight: 600, color: '#6b7280', marginTop: -2 }}>
            / 100
          </span>
        </div>
      </div>

      <div className="text-center">
        <p className="text-sm font-semibold text-gray-700">{label}</p>
        <p className="text-xs font-medium mt-0.5" style={{ color: textColor }}>{grade}</p>
      </div>
    </div>
  );
};

export default ScoreRing;
