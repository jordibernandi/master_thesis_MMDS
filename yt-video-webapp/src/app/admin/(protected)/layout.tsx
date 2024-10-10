import { SessionProvider } from "next-auth/react";
import { auth } from "@/auth";
import { Navbar } from "./_components/navbar";

interface AdminProtectedLayoutProps {
    children: React.ReactNode;
}

const AdminProtectedLayout = async ({ children }: AdminProtectedLayoutProps) => {
    const session = await auth();
    return (
        <SessionProvider session={session}>
            <Navbar />
            {children}
        </SessionProvider>
    );
}

export default AdminProtectedLayout;