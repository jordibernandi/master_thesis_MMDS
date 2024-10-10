"use client"

import { logout } from "@/actions/logout";
import FileUpload from "@/components/admin/file-upload";
import { useCurrentUser } from "@/hooks/use-current-user";

const SettingsPage = () => {
    const user = useCurrentUser();

    const onClick = () => {
        logout();
    }
    return (
        <div>
            <FileUpload />
        </div>
    );
}

export default SettingsPage;