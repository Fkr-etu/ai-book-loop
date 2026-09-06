import type { SVGProps } from "react";

type BrandMarkProps = SVGProps<SVGSVGElement> & {
  title?: string;
};

/** A loop, a book stitch, and the author's approval seal. */
export function BrandMark({ title, ...props }: BrandMarkProps) {
  return (
    <svg viewBox="0 0 40 40" role={title ? "img" : undefined} aria-hidden={title ? undefined : true} {...props}>
      {title && <title>{title}</title>}
      <path d="M11 8.5h10.2a7.3 7.3 0 0 1 0 14.6H15.5m13.5 8.4H18.8a7.3 7.3 0 0 1 0-14.6h5.7" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="4" />
      <path d="M20 10v20" fill="none" stroke="currentColor" strokeLinecap="round" strokeWidth="2" strokeDasharray="2 3" />
      <circle cx="20" cy="20" r="3.1" fill="var(--brand-seal, #d49a37)" stroke="var(--brand-paper, #fffdfc)" strokeWidth="1.5" />
    </svg>
  );
}
