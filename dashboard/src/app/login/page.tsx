'use client';

import { signIn } from 'next-auth/react';

export default function Login() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-discord_darker">
      <div className="bg-discord_dark p-8 rounded-2xl shadow-xl max-w-md w-full text-center border border-gray-800">
        <h2 className="text-3xl font-bold mb-6">Welcome Back</h2>
        <p className="text-gray-400 mb-8">Sign in to manage your Discord servers</p>
        <button
          onClick={() => signIn('discord', { callbackUrl: '/dashboard' })}
          className="w-full bg-blurple hover:bg-opacity-90 text-white font-bold py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          Login with Discord
        </button>
      </div>
    </div>
  );
}
