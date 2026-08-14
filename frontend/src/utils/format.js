export function formatPrice(value){
    return `${value.toLocaleString("ko-KR")}원`;
}

export function getTimeLeft(deadlineIso, now = new Date()){
    const diffMs = new Date(deadlineIso).getTime() - now.getTime();

    if (diffMs <= 0){
        return {label: "경매 종료", urgent: false, ended: true};
    }

    const totalSeconds = Math.floor(diffMs / 1000);
    const days = Math.floor(totalSeconds / 86400);
    const hours = Math.floor((totalSeconds % 86400) / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;

    const pad = (n) => String(n).padStart(2, "0");

    if (days >= 1) {
    return { label: `${days}일 ${pad(hours)}:${pad(minutes)} 남음`, urgent: false, ended: false };
    }

    const label = `${pad(hours)}:${pad(minutes)}:${pad(seconds)} 남음`;
  const urgent = totalSeconds < 3 * 3600;

    return { label, urgent, ended: false };
}