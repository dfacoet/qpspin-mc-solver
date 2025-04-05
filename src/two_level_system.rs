match (input_list.len(), input_list.first()) {
    (n, Some(first)) if n > 2 => {
        set.extend([1, 1, 2, 3, first.round() as u8]);
        let sum = input_list.iter().sum();
        Ok((set, if sum > 10.0 { Some(sum) } else { None }))
    },
    (_, _) => {
        let sum = input_list.iter().sum();
        Ok((set, if sum > 10.0 { Some(sum) } else { None }))
    }
}
