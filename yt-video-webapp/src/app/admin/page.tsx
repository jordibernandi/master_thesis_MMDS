import { Poppins } from "next/font/google";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { LoginButton } from "@/components/admin/login-button";

const font = Poppins({
    subsets: ["latin"],
    weight: ["600"]
})

const AdminPage = () => {
    return (
        <div className="space-y-6 text-center">
            <h1 className={cn("text-6xl font-semibold text-white drop-shadow-md", font.className)}>
                🔐 Auth
            </h1>
            <p className="text-white text-lg">
                Authenticate yourself !
            </p>
            <div>
                <LoginButton>
                    <Button variant="secondary" size="lg">
                        Sign in
                    </Button>
                </LoginButton>
            </div>
        </div>
    )
}

export default AdminPage;
