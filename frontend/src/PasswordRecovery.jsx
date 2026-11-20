import { useState } from "react";
import { request } from "./api";
import { Modal, Button, Logo } from "./ClinicUI";

function errorText(value) {
  return Array.isArray(value) ? value.join(" ") : String(value || "");
}

export function ForgotPasswordDialog({ onClose }) {
  const [pending, setPending] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");
  return (
    <Modal
      title="Forgot password"
      onClose={() => {
        if (!pending) onClose();
      }}
    >
      <form
        onSubmit={async (event) => {
          event.preventDefault();
          if (pending) return;
          const email = new FormData(event.currentTarget).get("email");
          setPending(true);
          setError("");
          try {
            await request("/api/auth/password/reset/", "POST", { email });
            setSent(true);
          } catch (e) {
            setError(errorText(e.body?.errors?.email) || e.message);
          } finally {
            setPending(false);
          }
        }}
        aria-busy={pending}
      >
        <div className="modal-content">
          {sent ? (
            <p role="status">
              A password-reset link has been sent to your registered email.
              Check your inbox and spam folder. The link expires in 30 minutes.
            </p>
          ) : (
            <>
              <p className="password-help">
                Enter the email address saved on your Clinic account, such as
                your Gmail address. We’ll email you a link to choose a new
                password.
              </p>
              <label className="field">
                Email address
                <input
                  name="email"
                  type="email"
                  autoComplete="email"
                  maxLength={254}
                  required
                  disabled={pending}
                />
              </label>
            </>
          )}
          {error && (
            <p className="notice" role="alert">
              {error}
            </p>
          )}
        </div>
        <div className="modal-actions">
          <Button variant="secondary" onClick={onClose} disabled={pending}>
            {sent ? "Back to login" : "Cancel"}
          </Button>
          {!sent && (
            <Button type="submit" disabled={pending}>
              {pending ? "Sending…" : "Send reset link"}
            </Button>
          )}
        </div>
      </form>
    </Modal>
  );
}

export function ResetPasswordForm({ link, onBack }) {
  const [pending, setPending] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");
  const [errors, setErrors] = useState({});
  return (
    <form
      className="login-form"
      aria-busy={pending}
      onSubmit={async (event) => {
        event.preventDefault();
        if (pending) return;
        const form = event.currentTarget;
        const data = Object.fromEntries(new FormData(form));
        setError("");
        setErrors({});
        if (data.new_password !== data.confirm_password) {
          setErrors({ confirm_password: ["The passwords do not match."] });
          return;
        }
        setPending(true);
        try {
          await request("/api/auth/password/reset/confirm/", "POST", {
            uid: link.uid,
            token: link.token,
            ...data,
          });
          form.reset();
          setDone(true);
        } catch (e) {
          setError(e.message);
          setErrors(e.body?.errors || {});
        } finally {
          setPending(false);
        }
      }}
    >
      <div className="login-brand">
        <Logo />
      </div>
      <h2>{done ? "Password reset complete" : "Reset your password"}</h2>
      {done ? (
        <>
          <p role="status">
            Your password has been reset. Your previous sessions have been
            signed out. Log in with your new password.
          </p>
          <Button onClick={onBack}>Back to login</Button>
        </>
      ) : (
        <>
          <p>
            Choose a strong new password with at least 8 characters. Avoid
            common passwords and passwords similar to your account details.
          </p>
          {[
            ["new_password", "New password"],
            ["confirm_password", "Confirm new password"],
          ].map(([name, label]) => (
            <label className="field" key={name}>
              {label}
              <input
                name={name}
                aria-label={label}
                type="password"
                autoComplete="new-password"
                required
                maxLength={1024}
                disabled={pending}
                aria-invalid={!!errors[name]}
                aria-describedby={errors[name] ? `${name}-error` : undefined}
              />
              {errors[name] && (
                <span role="alert" id={`${name}-error`}>
                  {errorText(errors[name])}
                </span>
              )}
            </label>
          ))}
          {error && (
            <p className="notice" role="alert">
              {errorText(errors.token) || error}
            </p>
          )}
          <Button type="submit" disabled={pending}>
            {pending ? "Resetting…" : "Reset password"}
          </Button>
          <Button variant="secondary" onClick={onBack} disabled={pending}>
            Back to login
          </Button>
        </>
      )}
    </form>
  );
}
