use std::env;

enum Filesize {
    Bytes(u64),
    Kilobytes(u64),
    Megabytes(u64),
    Gigabytes(u64),
    Terabytes(u64),
}

impl Filesize {
    fn parse_input(args: &Vec<String>) -> Filesize {
        if args.len() < 2 {
            panic!("not enough arguments. pass something like '256 mb', or just an integer as you want to pass size in bytes.");
        }

        let amount = args[1]
            .parse::<u64>()
            .expect("filed to parse filesize amount as u64");

        let filesize = if args.len() > 2 {
            match args[2].as_str() {
                "kb" => Filesize::Kilobytes(amount),
                "mb" => Filesize::Megabytes(amount),
                "gb" => Filesize::Gigabytes(amount),
                "tb" => Filesize::Terabytes(amount),
                _ => Filesize::Bytes(amount),
            }
        } else {
            Filesize::Bytes(amount)
        };

        filesize
    }

    fn to_bytes(&self) -> u64 {
        match *self {
            Filesize::Bytes(b) => b,
            Filesize::Kilobytes(kb) => kb * 1_000,
            Filesize::Megabytes(mb) => mb * 1_000_000,
            Filesize::Gigabytes(gb) => gb * 1_000_000_000,
            Filesize::Terabytes(tb) => tb * 1_000_000_000_000,
        }
    }
}

#[derive(Debug)]
struct ComparedSizes {
    bytes: u64,
    kilo_bytes: f64,
    mega_bytes: f64,
    giga_bytes: f64,
    tera_bytes: f64,
}

impl ComparedSizes {
    fn from_filesize(filesize: Filesize) -> ComparedSizes {
        let bytes = filesize.to_bytes();

        ComparedSizes {
            bytes,
            kilo_bytes: bytes as f64 / 1000.0,
            mega_bytes: bytes as f64 / 1_000_000.0,
            giga_bytes: bytes as f64 / 1_000_000_000.0,
            tera_bytes: bytes as f64 / 1_000_000_000_000.0,
        }
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let input = Filesize::parse_input(&args);
    let compared = ComparedSizes::from_filesize(input);

    println!("{:?}", compared);
}
