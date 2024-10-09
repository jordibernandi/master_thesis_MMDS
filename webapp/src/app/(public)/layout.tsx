import styles from "./layout.module.css";
import { SessionProvider } from "next-auth/react";
import { auth } from "@/auth";
import Navbar from "@/components/navbar/Navbar";
import Footer from "@/components/footer/Footer";

interface PublicLayoutProps {
    children: React.ReactNode;
}

const PublicLayout = async ({ children }: PublicLayoutProps) => {
    const session = await auth();
    return (
        <main className="bg-[#FEFEFE]">
            <SessionProvider session={session}>
                <div className={styles.container}>
                    <Navbar />
                    {children}
                    <Footer />
                </div>
            </SessionProvider>
        </main>
    );
}

export default PublicLayout;