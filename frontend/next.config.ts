import type { NextConfig } from "next";
import dotenv from "dotenv";
import path from "path";

dotenv.config({
  path: path.join(__dirname, "../.env")
})

const nextConfig: NextConfig = {
  /* config options here */
};

export default nextConfig;
