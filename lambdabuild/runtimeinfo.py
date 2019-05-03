RUNTIMES = {
    '2.7': dict(
        base_image="lambci/lambda:build-python2.7",
        two_or_three="2",
        three="",
    ),
    '3.6': dict(
        base_image="lambci/lambda:build-python3.6",
        two_or_three="3",
        three="3",
    ),
    '3.7': dict(
        base_image="lambci/lambda:build-python3.7",
        two_or_three="3",
        three="3",
    ),
}

BASE_IMAGES = [
    "lambci/lambda:build-python3.6",
    "lambci/lambda:build-python3.7",
    "lambci/lambda:build-python2.7",
    "amazonlinux:2017.03",
]
