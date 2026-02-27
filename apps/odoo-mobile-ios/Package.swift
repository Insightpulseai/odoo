// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "OdooMobile",
    platforms: [
        .iOS(.v17)
    ],
    products: [
        .library(
            name: "OdooMobile",
            targets: ["OdooMobile"]
        )
    ],
    targets: [
        .target(
            name: "OdooMobile",
            path: "Sources"
        ),
        .testTarget(
            name: "OdooMobileTests",
            dependencies: ["OdooMobile"],
            path: "Tests"
        )
    ]
)
