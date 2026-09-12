import Image from "next/image";

type BrandMarkProps = {
  className?: string;
  title?: string;
};

/** The official Book Loop symbol, used wherever the compact brand mark is needed. */
export function BrandMark({ className, title = "Book Loop" }: BrandMarkProps) {
  return (
    <Image
      src="/brand/symbol-transparent.svg"
      alt={title}
      width={170}
      height={170}
      className={className}
    />
  );
}
