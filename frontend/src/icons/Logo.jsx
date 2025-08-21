export default function Logo({ className = "w-8 h-8" }) {
  return (
    <svg className={className} viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" aria-hidden>
      <defs>
        <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#6366f1"/>
          <stop offset="100%" stopColor="#22d3ee"/>
        </linearGradient>
      </defs>
      <rect rx="40" width="200" height="200" fill="url(#g)"/>
      <g fill="white" transform="translate(40,40)">
        <circle cx="30" cy="30" r="12"/>
        <circle cx="90" cy="30" r="12"/>
        <rect x="18" y="70" width="96" height="20" rx="10"/>
      </g>
    </svg>
  );
}
