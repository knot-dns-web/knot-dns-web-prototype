"use client";

import { Modal } from "./Modal";

type ConfirmDialogProps = {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
};

export function ConfirmDialog({
  open,
  onClose,
  onConfirm,
  title,
  message,
  confirmLabel = "Удалить",
  cancelLabel = "Отмена",
}: ConfirmDialogProps) {
  return (
    <Modal
      open={open}
      onClose={onClose}
      title={title}
      footer={
        <>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-slate-600 px-4 py-2 text-sm text-slate-300 hover:bg-white/5"
          >
            {cancelLabel}
          </button>
          <button
            type="button"
            onClick={async () => {
              try {
                await Promise.resolve(onConfirm());
                onClose();
              } catch {
                /* ошибка — окно остаётся открытым */
              }
            }}
            className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-500"
          >
            {confirmLabel}
          </button>
        </>
      }
    >
      <p className="text-sm text-slate-400">{message}</p>
    </Modal>
  );
}
