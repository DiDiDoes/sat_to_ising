echo "Start with num_reads=10, sweeping through different num_sweeps values."
for num_sweep in 100 500 1000 2000 5000 10000; do
    echo "Running Neal with num_sweep=$num_sweep"
    python run_neal.py --num-instance 100 --num-sweeps $num_sweep --num-reads 10
done

echo "Fix num_sweeps=2000, sweeping through different num_reads values."
for num_read in 1 5 10 20 50 100; do
    echo "Running Neal with num_reads=$num_read"
    python run_neal.py --num-instance 100 --num-sweeps 2000 --num-reads $num_read
done
