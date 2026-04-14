"use client";

import useRegister from "@/features/auth/register/application/useRegister";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import {
  FaFacebookF,
  FaGoogle,
  FaTwitter,
  FaUser,
  FaLock,
  FaEnvelope,
} from "react-icons/fa";

export default function RegisterPage() {
  const { execute: performRegister, loading, error } = useRegister();
  const router = useRouter();

  const [form, setForm] = useState({
    username: "",
    email: "",
    first_name: "",
    last_name: "",
    password: "",
    phone_number: "",
  });

  const [rememberMe, setRememberMe] = useState(false);
  const [localError, setLocalError] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    setLocalError("");

    try {
      await performRegister(form);
      alert("Registration successful! Please login.");
      router.push("/login");
    } catch (err) {
      console.error(err);
      setLocalError(err?.message || "Registration failed.");
    }
  };

  return (
    <div className="min-h-screen bg-red-400">
      <div
        className="min-h-screen w-full bg-cover bg-center bg-no-repeat px-4 py-8 md:px-8 md:py-12"
        style={{ backgroundImage: "url('https://placehold.co/1440x1024')" }}
      >
        <div className="mx-auto flex w-full max-w-[1236px] flex-col overflow-hidden rounded-[10px] bg-white shadow-[5px_4px_14px_0px_rgba(0,0,0,0.04),20px_16px_26px_0px_rgba(0,0,0,0.03),45px_36px_34px_0px_rgba(0,0,0,0.02),80px_64px_41px_0px_rgba(0,0,0,0.01),124px_100px_45px_0px_rgba(0,0,0,0)] lg:min-h-[767px] lg:flex-row">
          <div className="flex w-full flex-col justify-center p-6 md:p-10 lg:w-1/2 lg:p-14">
            <h1 className="mb-8 text-4xl font-bold text-neutral-800">Sign In</h1>

            <form onSubmit={handleRegisterSubmit} className="space-y-4">
              <div className="relative">
                <FaUser className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-neutral-800" />
                <input
                  type="text"
                  name="username"
                  placeholder="Enter Username"
                  value={form.username}
                  onChange={handleChange}
                  className="h-14 w-full rounded-lg border border-neutral-600 px-12 text-base font-medium text-neutral-800 placeholder:text-neutral-400 focus:border-neutral-700 focus:outline-none"
                  required
                />
              </div>

              <div className="relative">
                <FaEnvelope className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-neutral-800" />
                <input
                  type="email"
                  name="email"
                  placeholder="Enter Email"
                  value={form.email}
                  onChange={handleChange}
                  className="h-14 w-full rounded-lg border border-neutral-600 px-12 text-base font-medium text-neutral-800 placeholder:text-neutral-400 focus:border-neutral-700 focus:outline-none"
                  required
                />
              </div>

              <div className="relative">
                <FaLock className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-neutral-800" />
                <input
                  type="password"
                  name="password"
                  placeholder="Enter Password"
                  value={form.password}
                  onChange={handleChange}
                  className="h-14 w-full rounded-lg border border-neutral-600 px-12 text-base font-medium text-neutral-800 placeholder:text-neutral-400 focus:border-neutral-700 focus:outline-none"
                  required
                />
              </div>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <input
                  type="text"
                  name="first_name"
                  placeholder="Enter First Name"
                  value={form.first_name}
                  onChange={handleChange}
                  className="h-14 w-full rounded-lg border border-neutral-600 px-4 text-base font-medium text-neutral-800 placeholder:text-neutral-400 focus:border-neutral-700 focus:outline-none"
                />
                <input
                  type="text"
                  name="last_name"
                  placeholder="Enter Last Name"
                  value={form.last_name}
                  onChange={handleChange}
                  className="h-14 w-full rounded-lg border border-neutral-600 px-4 text-base font-medium text-neutral-800 placeholder:text-neutral-400 focus:border-neutral-700 focus:outline-none"
                />
              </div>

              <input
                type="text"
                name="phone_number"
                placeholder="Enter Phone Number (optional)"
                value={form.phone_number}
                onChange={handleChange}
                className="h-14 w-full rounded-lg border border-neutral-600 px-4 text-base font-medium text-neutral-800 placeholder:text-neutral-400 focus:border-neutral-700 focus:outline-none"
              />

              <label className="flex items-center gap-3 pt-1 text-base font-medium text-neutral-800">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="h-[18px] w-[18px] rounded border border-[#565454]"
                />
                Remember Me
              </label>

              {(localError || error) && (
                <p className="text-sm text-red-600">{localError || error}</p>
              )}

              <button
                type="submit"
                disabled={loading}
                className="h-14 w-32 rounded-[5px] bg-red-300 text-base font-medium text-slate-50 transition hover:bg-red-400 disabled:cursor-not-allowed disabled:opacity-70"
              >
                {loading ? "Registering..." : "Login"}
              </button>
            </form>

            <div className="mt-14">
              <p className="mb-4 text-base font-medium text-neutral-800">Or, Login with</p>
              <div className="flex items-center gap-5">
                <button type="button" className="text-[27px] text-black">
                  <FaTwitter />
                </button>
                <button
                  type="button"
                  className="flex h-7 w-7 items-center justify-center rounded bg-[#3D5A98] text-white"
                >
                  <FaFacebookF className="text-sm" />
                </button>
                <button type="button" className="text-[25px] text-black">
                  <FaGoogle />
                </button>
              </div>
            </div>

            <p className="mt-4 text-base font-medium text-neutral-800">
              Don’t have an account?{" "}
              <Link href="/register" className="text-sky-600">
                Create One
              </Link>
            </p>
          </div>

          <div className="hidden w-full items-center justify-center bg-white p-6 lg:flex lg:w-1/2">
            <img
              src="https://placehold.co/613x613"
              alt="Auth Visual"
              className="h-auto w-full max-w-[613px] object-contain"
            />
          </div>
        </div>
      </div>
    </div>
  );
}