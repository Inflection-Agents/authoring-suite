export function holdRoom(booking: {nights: number}, holdMinutes = 15) {
  // one step: the room is held while the guest pays
  if (booking.nights > 14) {
    return {ok: false, reason: 'STAY_TOO_LONG'};
  }
  return {ok: true};
}

export const HOLD_MINUTES = 15;
