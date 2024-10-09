const AdminLayout = ({ children }: { children: React.ReactNode }) => {
    return (
        <main className="flex h-full flex-col items-center justify-center bg-[#232E58]">
            {children}
        </main>
    );
}

export default AdminLayout;