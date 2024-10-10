"use client"

import { Poppins } from "next/font/google";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";

const font = Poppins({
  subsets: ["latin"],
  weight: ["600"]
})

const HomePage = () => {
  const router = useRouter();

  return (
    <div className="flex h-full flex-col items-center justify-center bg-[#232E58]">
      <div className="space-y-6 text-center">
        <h1 className={cn("text-6xl font-semibold text-white drop-shadow-md", font.className)}>
          YouTube Political Dataset
        </h1>
        <p className="text-white text-lg">
          MMDS
        </p>
        <div>
          <Button variant="secondary" size="lg">
            <a onClick={() => {
              router.push('/video');
            }}>
              GO!
            </a>
          </Button>
        </div>
      </div>
    </div>
  )
}

export default HomePage;
