"use client"

import styles from "./navbar.module.css";

import Link from "next/link"

const Navbar = () => {

    return (
        <div className={styles.container}>
            <Link href="/video" className={styles.logo}>MMDS</Link>
            <div className={styles.container}>

            </div>
        </div>
    )
}

export default Navbar