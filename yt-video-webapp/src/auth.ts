import NextAuth from "next-auth";
import authConfig from "@/auth.config";
import { PrismaAdapter } from "@auth/prisma-adapter";
import { UserRole } from "@prisma/client";
import { db } from "@/lib/db";
import { getUserById } from "@/data/user";

declare module "@auth/core/types" {
    interface Session {
        // add your custom fields here
        user: {
            role: string;
        } & DefaultSession["user"]
    }
}

export const {
    handlers: { GET, POST },
    auth,
    signIn,
    signOut
} = NextAuth({
    callbacks: {
        async signIn({ user, account }) {
            // // Allow OAuth without email verification
            // if (account?.provider !== "credentials") return true;

            // const existingUser = await getUserById(user.id ?? '');

            // // Prevent sign in without email verification
            // if (!existingUser?.emailVerified) return false;

            return true;
        },
        async session({ token, session }) {
            if (token.sub && session.user) {
                session.user.id = token.sub;
            }

            // if (token.role && session.user) {
            //     session.user.role = token.role as UserRole;
            // }

            if (session.user) {
                session.user.name = token.name;
            }

            return session;
        },
        async jwt({ token }) {
            if (!token.sub) return token;

            const existingUser = await getUserById(token.sub);

            if (!existingUser) return token;

            token.name = existingUser.name;
            token.email = existingUser.email;
            token.role = existingUser.role;

            return token;
        }
    },
    adapter: PrismaAdapter(db),
    session: { strategy: "jwt" },
    ...authConfig
});