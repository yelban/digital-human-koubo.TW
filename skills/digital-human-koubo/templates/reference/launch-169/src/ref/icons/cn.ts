// lucide-animated 原始碼裡的 cn()（原為 clsx + tailwind-merge），這裡只需拼 className
export const cn = (...a: any[]) => a.flat(Infinity as 1).filter(Boolean).join(" ");
