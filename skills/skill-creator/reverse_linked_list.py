class ListNode:
    def __init__(self, value=0, next=None):
        self.value = value
        self.next = next


def reverse_linked_list(head):
    """Reverse a singly linked list iteratively. Returns the new head."""
    prev = None
    current = head
    while current is not None:
        next_node = current.next
        current.next = prev
        prev = current
        current = next_node
    return prev


def to_list(head):
    values = []
    while head is not None:
        values.append(head.value)
        head = head.next
    return values


def from_list(values):
    head = ListNode()
    current = head
    for v in values:
        current.next = ListNode(v)
        current = current.next
    return head.next


if __name__ == "__main__":
    # sanity check: 1 -> 2 -> 3 becomes 3 -> 2 -> 1
    original = [1, 2, 3]
    head = from_list(original)
    reversed_head = reverse_linked_list(head)
    result = to_list(reversed_head)
    assert result == original[::-1], result
    print("reversed:", result)
