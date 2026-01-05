export class RingBuffer<T extends { t: number }> {
  private buf: T[] = [];
  constructor(private max: number) {}

  push(v: T) {
    this.buf.push(v);
    if (this.buf.length > this.max) this.buf.shift();
  }

  since(t: number) {
    return this.buf.filter(x => x.t >= t);
  }
}