"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface Option {
  value: string;
  label: string;
}

interface ParamSelectProps {
  paramName: string;
  value: string;
  options: Option[];
  placeholder?: string;
  className?: string;
}

export function ParamSelect({
  paramName,
  value,
  options,
  placeholder,
  className,
}: ParamSelectProps) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  function handleChange(nextValue: string | null) {
    if (nextValue === null) return;

    const params = new URLSearchParams(searchParams.toString());
    params.set(paramName, nextValue);
    router.push(`${pathname}?${params.toString()}`);
  }

  return (
    <Select value={value} onValueChange={handleChange}>
      <SelectTrigger className={className ?? "w-full sm:w-64"}>
        <SelectValue placeholder={placeholder ?? "Select..."}>
          {(val: string | null) =>
            options.find((option) => option.value === val)?.label ?? placeholder ?? "Select..."
          }
        </SelectValue>
      </SelectTrigger>
      <SelectContent>
        {options.map((option) => (
          <SelectItem key={option.value} value={option.value}>
            {option.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
