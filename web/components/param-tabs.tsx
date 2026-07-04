"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";

import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface Option {
  value: string;
  label: string;
}

interface ParamTabsProps {
  paramName: string;
  value: string;
  options: Option[];
}

export function ParamTabs({ paramName, value, options }: ParamTabsProps) {
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
    <Tabs value={value} onValueChange={handleChange}>
      <TabsList>
        {options.map((option) => (
          <TabsTrigger key={option.value} value={option.value}>
            {option.label}
          </TabsTrigger>
        ))}
      </TabsList>
    </Tabs>
  );
}
