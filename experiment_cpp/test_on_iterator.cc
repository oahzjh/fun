#include <algorithm>
#include <iterator>
#include <iostream>

struct FunctionRecord
{
	void const *trampolineFunction;
	void **thunkSeat;
};

FunctionRecord const func_array[] = { 
	{
		.trampolineFunction = nullptr,
		.thunkSeat = nullptr,
	},
	{
		.trampolineFunction = nullptr,
		.thunkSeat = nullptr,
	}
};

int main(int argc, char* argv[]) 
{
	(void)argc;
	(void)argv;

	std::cout << "hello, what ever\n";
	std::cout << std::begin(func_array) << std::endl;
	std::cout << std::end(func_array) << std::endl;
	auto found = std::find_if(std::begin(func_array),
							  std::end(func_array),
							  [=](FunctionRecord const &fr) {
							  return fr.trampolineFunction == nullptr;
							  });

	std::cout << "Found: " << found << std::endl;
	std::cout << "bye, what ever\n";
	return 0;
}
